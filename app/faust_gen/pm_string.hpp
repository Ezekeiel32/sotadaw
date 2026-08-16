/* ------------------------------------------------------------
name: "pm_string"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn PmString -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __PmString_H__
#define  __PmString_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS PmString
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

static float PmString_faustpower2_f(float value) {
	return value * value;
}

class PmString : public dsp {
	
 private:
	
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst4;
	float fConst6;
	FAUSTFLOAT fHslider0;
	float fConst7;
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iRec3[2];
	float fConst8;
	float fConst9;
	float fConst10;
	int iRec4[2];
	int IOTA0;
	float fVec1[4096];
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	float fRec2[3];
	float fRec5[2];
	FAUSTFLOAT fHslider3;
	float fVec2[8192];
	float fRec1[3];
	float fRec0[3];
	float fConst11;
	float fConst13;
	float fConst15;
	float fConst17;
	float fRec6[3];
	float fConst18;
	FAUSTFLOAT fHslider4;
	FAUSTFLOAT fHslider5;
	
 public:
	PmString() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn PmString -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("delays.lib/fdelay4:author", "Julius O. Smith III");
		m->declare("delays.lib/fdelayltv:author", "Julius O. Smith III");
		m->declare("delays.lib/name", "Faust Delay Library");
		m->declare("delays.lib/version", "1.1.0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "pm_string.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "pm_string");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(706.85834f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / PmString_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -0.2f) / fConst1 + 1.0f;
		float fConst5 = (fConst3 + 0.2f) / fConst1 + 1.0f;
		fConst6 = 1.0f / fConst5;
		fConst7 = 3.1415927f / fConst0;
		fConst8 = std::max<float>(1.0f, 0.0005f * fConst0);
		fConst9 = 1.0f / fConst8;
		fConst10 = 1.0f / std::max<float>(1.0f, 0.004f * fConst0);
		fConst11 = 0.28f / (fConst1 * fConst5);
		float fConst12 = std::tan(345.5752f / fConst0);
		fConst13 = 2.0f * (1.0f - 1.0f / PmString_faustpower2_f(fConst12));
		float fConst14 = 1.0f / fConst12;
		fConst15 = (fConst14 + -0.25f) / fConst12 + 1.0f;
		float fConst16 = (fConst14 + 0.25f) / fConst12 + 1.0f;
		fConst17 = 1.0f / fConst16;
		fConst18 = 0.35f / (fConst12 * fConst16);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.45f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(2.2e+02f);
		fHslider2 = FAUSTFLOAT(0.24f);
		fHslider3 = FAUSTFLOAT(0.6f);
		fHslider4 = FAUSTFLOAT(0.35f);
		fHslider5 = FAUSTFLOAT(0.8f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec3[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec4[l2] = 0;
		}
		IOTA0 = 0;
		for (int l3 = 0; l3 < 4096; l3 = l3 + 1) {
			fVec1[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec5[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 8192; l6 = l6 + 1) {
			fVec2[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 3; l7 = l7 + 1) {
			fRec1[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 3; l8 = l8 + 1) {
			fRec0[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 3; l9 = l9 + 1) {
			fRec6[l9] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual PmString* clone() {
		return new PmString();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("pm_string");
		ui_interface->addHorizontalSlider("body", &fHslider4, FAUSTFLOAT(0.35f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("damp", &fHslider0, FAUSTFLOAT(0.45f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider1, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(27.0f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("pluck", &fHslider2, FAUSTFLOAT(0.24f), FAUSTFLOAT(0.05f), FAUSTFLOAT(0.5f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("sustain", &fHslider3, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::tan(fConst7 * (8.8e+03f * float(fHslider0) + 1.2e+03f));
		float fSlow1 = 2.0f * (1.0f - 1.0f / PmString_faustpower2_f(fSlow0));
		float fSlow2 = 1.0f / fSlow0;
		float fSlow3 = (fSlow2 + -1.4142135f) / fSlow0 + 1.0f;
		float fSlow4 = 1.0f / ((fSlow2 + 1.4142135f) / fSlow0 + 1.0f);
		float fSlow5 = float(fButton0);
		float fSlow6 = std::max<float>(27.0f, float(fHslider1));
		int iSlow7 = int(std::max<float>(1.0f, fConst0 * (float(fHslider2) / fSlow6)));
		float fSlow8 = 1.0f - fSlow2;
		float fSlow9 = 1.0f / (fSlow2 + 1.0f);
		float fSlow10 = 0.0135f * float(fHslider3) + 0.985f;
		float fSlow11 = std::max<float>(2.0f, fConst0 / fSlow6 + -2.0f);
		float fSlow12 = fSlow11 + -1.499995f;
		int iSlow13 = int(fSlow12);
		int iSlow14 = std::min<int>(8192, std::max<int>(0, iSlow13 + 4));
		float fSlow15 = std::floor(fSlow12);
		float fSlow16 = fSlow11 + (-3.0f - fSlow15);
		float fSlow17 = fSlow11 + (-2.0f - fSlow15);
		float fSlow18 = fSlow11 + (-1.0f - fSlow15);
		float fSlow19 = fSlow11 - fSlow15;
		float fSlow20 = fSlow19 * fSlow18;
		float fSlow21 = fSlow20 * fSlow17;
		float fSlow22 = 0.041666668f * fSlow21 * fSlow16;
		int iSlow23 = std::min<int>(8192, std::max<int>(0, iSlow13 + 3));
		float fSlow24 = 0.16666667f * fSlow21;
		int iSlow25 = std::min<int>(8192, std::max<int>(0, iSlow13 + 2));
		float fSlow26 = 0.25f * fSlow20;
		int iSlow27 = std::min<int>(8192, std::max<int>(0, iSlow13 + 1));
		float fSlow28 = 0.16666667f * fSlow19;
		int iSlow29 = std::min<int>(8192, std::max<int>(0, iSlow13));
		float fSlow30 = 0.041666668f * fSlow18;
		float fSlow31 = fSlow11 + (-4.0f - fSlow15);
		float fSlow32 = float(fHslider4);
		float fSlow33 = 1.0f - 0.6f * fSlow32;
		float fSlow34 = 0.7f * float(fHslider5);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow5;
			iRec3[0] = (iRec3[1] + (iRec3[1] > 0)) * (fSlow5 <= fVec0[1]) + (fSlow5 > fVec0[1]);
			float fTemp0 = float(iRec3[0]);
			iRec4[0] = 1103515245 * iRec4[1] + 12345;
			float fTemp1 = float(iRec4[0]) * std::max<float>(0.0f, std::min<float>(fConst9 * fTemp0, fConst10 * (fConst8 - fTemp0) + 1.0f));
			fVec1[IOTA0 & 4095] = fTemp1;
			fRec2[0] = 2.3283064e-10f * (fTemp1 - fVec1[(IOTA0 - iSlow7) & 4095]) - fSlow4 * (fSlow3 * fRec2[2] + fSlow1 * fRec2[1]);
			fRec5[0] = -(fSlow9 * (fSlow8 * fRec5[1] - (fRec1[1] + fRec1[2])));
			float fTemp2 = fSlow10 * fRec5[0] + fSlow4 * (fRec2[2] + fRec2[0] + 2.0f * fRec2[1]);
			fVec2[IOTA0 & 8191] = fTemp2;
			fRec1[0] = fSlow31 * (fSlow16 * (fSlow17 * (fSlow30 * fVec2[(IOTA0 - iSlow29) & 8191] - fSlow28 * fVec2[(IOTA0 - iSlow27) & 8191]) + fSlow26 * fVec2[(IOTA0 - iSlow25) & 8191]) - fSlow24 * fVec2[(IOTA0 - iSlow23) & 8191]) + fSlow22 * fVec2[(IOTA0 - iSlow14) & 8191];
			fRec0[0] = fRec1[0] - fConst6 * (fConst4 * fRec0[2] + fConst2 * fRec0[1]);
			fRec6[0] = fRec1[0] - fConst17 * (fConst15 * fRec6[2] + fConst13 * fRec6[1]);
			float fTemp3 = fSlow34 * (fSlow33 * fRec1[0] + fSlow32 * (fConst18 * (fRec6[0] - fRec6[2]) + fConst11 * (fRec0[0] - fRec0[2])));
			output0[i0] = FAUSTFLOAT(fTemp3);
			output1[i0] = FAUSTFLOAT(fTemp3);
			fVec0[1] = fVec0[0];
			iRec3[1] = iRec3[0];
			iRec4[1] = iRec4[0];
			IOTA0 = IOTA0 + 1;
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			fRec5[1] = fRec5[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
			fRec6[2] = fRec6[1];
			fRec6[1] = fRec6[0];
		}
	}

};

#endif
