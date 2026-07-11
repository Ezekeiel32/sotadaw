/* ------------------------------------------------------------
name: "oud"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Oud -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Oud_H__
#define  __Oud_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Oud
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

static float Oud_faustpower2_f(float value) {
	return value * value;
}

class Oud : public dsp {
	
 private:
	
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst4;
	float fConst5;
	float fConst7;
	float fConst9;
	float fConst11;
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iRec2[2];
	float fConst12;
	float fConst13;
	float fConst14;
	int iRec3[2];
	FAUSTFLOAT fHslider0;
	float fRec1[3];
	float fConst15;
	FAUSTFLOAT fHslider1;
	float fConst16;
	FAUSTFLOAT fHslider2;
	float fConst17;
	float fRec6[2];
	FAUSTFLOAT fHslider3;
	int IOTA0;
	float fVec1[4096];
	float fRec5[3];
	float fRec4[3];
	FAUSTFLOAT fHslider4;
	float fRec0[3];
	
 public:
	Oud() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn Oud -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
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
		m->declare("filename", "oud.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/resonlp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonlp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonlp:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "oud");
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
		float fConst1 = std::tan(16336.282f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / Oud_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -1.4142135f) / fConst1 + 1.0f;
		fConst5 = 1.0f / ((fConst3 + 1.4142135f) / fConst1 + 1.0f);
		float fConst6 = std::tan(5654.8667f / fConst0);
		fConst7 = 2.0f * (1.0f - 1.0f / Oud_faustpower2_f(fConst6));
		float fConst8 = 1.0f / fConst6;
		fConst9 = (fConst8 + -0.6666667f) / fConst6 + 1.0f;
		float fConst10 = (fConst8 + 0.6666667f) / fConst6 + 1.0f;
		fConst11 = 1.0f / fConst10;
		fConst12 = std::max<float>(1.0f, 0.0005f * fConst0);
		fConst13 = 1.0f / fConst12;
		fConst14 = 1.0f / std::max<float>(1.0f, 0.006f * fConst0);
		fConst15 = 1.0f / (fConst6 * fConst10);
		fConst16 = 6.911504f / fConst0;
		fConst17 = 3.1415927f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.4f);
		fHslider1 = FAUSTFLOAT(2.2e+02f);
		fHslider2 = FAUSTFLOAT(2.4e+03f);
		fHslider3 = FAUSTFLOAT(0.994f);
		fHslider4 = FAUSTFLOAT(0.6f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec2[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec3[l2] = 0;
		}
		for (int l3 = 0; l3 < 3; l3 = l3 + 1) {
			fRec1[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec6[l4] = 0.0f;
		}
		IOTA0 = 0;
		for (int l5 = 0; l5 < 4096; l5 = l5 + 1) {
			fVec1[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 3; l6 = l6 + 1) {
			fRec5[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 3; l7 = l7 + 1) {
			fRec4[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 3; l8 = l8 + 1) {
			fRec0[l8] = 0.0f;
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
	
	virtual Oud* clone() {
		return new Oud();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("oud");
		ui_interface->addHorizontalSlider("freq", &fHslider1, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(6e+01f), FAUSTFLOAT(1.2e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("pick", &fHslider0, FAUSTFLOAT(0.4f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("ring", &fHslider3, FAUSTFLOAT(0.994f), FAUSTFLOAT(0.98f), FAUSTFLOAT(0.999f), FAUSTFLOAT(0.0001f));
		ui_interface->addHorizontalSlider("warmth", &fHslider2, FAUSTFLOAT(2.4e+03f), FAUSTFLOAT(8e+02f), FAUSTFLOAT(6e+03f), FAUSTFLOAT(1.0f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		float fSlow1 = 4.656613e-10f * float(fHslider0);
		float fSlow2 = float(fHslider1);
		float fSlow3 = std::tan(fConst16 * fSlow2);
		float fSlow4 = 2.0f * (1.0f - 1.0f / Oud_faustpower2_f(fSlow3));
		float fSlow5 = 1.0f / fSlow3;
		float fSlow6 = (fSlow5 + -0.8333333f) / fSlow3 + 1.0f;
		float fSlow7 = 1.0f / ((fSlow5 + 0.8333333f) / fSlow3 + 1.0f);
		float fSlow8 = 1.0f / std::tan(fConst17 * float(fHslider2));
		float fSlow9 = 1.0f - fSlow8;
		float fSlow10 = 1.0f / (fSlow8 + 1.0f);
		float fSlow11 = float(fHslider3);
		float fSlow12 = fConst0 / fSlow2;
		float fSlow13 = fSlow12 + -2.499995f;
		int iSlow14 = int(fSlow13);
		int iSlow15 = std::min<int>(4096, std::max<int>(0, iSlow14 + 4));
		float fSlow16 = std::floor(fSlow13);
		float fSlow17 = fSlow12 + (-4.0f - fSlow16);
		float fSlow18 = fSlow12 + (-3.0f - fSlow16);
		float fSlow19 = fSlow12 + (-2.0f - fSlow16);
		float fSlow20 = fSlow12 + (-1.0f - fSlow16);
		float fSlow21 = fSlow20 * fSlow19;
		float fSlow22 = fSlow21 * fSlow18;
		float fSlow23 = 0.041666668f * fSlow22 * fSlow17;
		int iSlow24 = std::min<int>(4096, std::max<int>(0, iSlow14 + 3));
		float fSlow25 = 0.16666667f * fSlow22;
		int iSlow26 = std::min<int>(4096, std::max<int>(0, iSlow14 + 2));
		float fSlow27 = 0.25f * fSlow21;
		int iSlow28 = std::min<int>(4096, std::max<int>(0, iSlow14 + 1));
		float fSlow29 = 0.16666667f * fSlow20;
		int iSlow30 = std::min<int>(4096, std::max<int>(0, iSlow14));
		float fSlow31 = 0.041666668f * fSlow19;
		float fSlow32 = fSlow12 + (-5.0f - fSlow16);
		float fSlow33 = 0.7f * float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow0;
			iRec2[0] = (iRec2[1] + (iRec2[1] > 0)) * (fSlow0 <= fVec0[1]) + (fSlow0 > fVec0[1]);
			float fTemp0 = float(iRec2[0]);
			iRec3[0] = 1103515245 * iRec3[1] + 12345;
			float fTemp1 = float(iRec3[0]) * std::max<float>(0.0f, std::min<float>(fConst13 * fTemp0, fConst14 * (fConst12 - fTemp0) + 1.0f));
			fRec1[0] = fSlow1 * fTemp1 - fConst11 * (fConst9 * fRec1[2] + fConst7 * fRec1[1]);
			fRec6[0] = -(fSlow10 * (fSlow9 * fRec6[1] - (fRec5[1] + fRec5[2])));
			float fTemp2 = fSlow11 * fRec6[0] + 4.656613e-10f * fTemp1;
			fVec1[IOTA0 & 4095] = fTemp2;
			fRec5[0] = fSlow32 * (fSlow17 * (fSlow18 * (fSlow31 * fVec1[(IOTA0 - iSlow30) & 4095] - fSlow29 * fVec1[(IOTA0 - iSlow28) & 4095]) + fSlow27 * fVec1[(IOTA0 - iSlow26) & 4095]) - fSlow25 * fVec1[(IOTA0 - iSlow24) & 4095]) + fSlow23 * fVec1[(IOTA0 - iSlow15) & 4095];
			fRec4[0] = fRec5[0] - fSlow7 * (fSlow6 * fRec4[2] + fSlow4 * fRec4[1]);
			fRec0[0] = fSlow33 * (fSlow7 * (fRec4[2] + fRec4[0] + 2.0f * fRec4[1]) + fConst15 * (fRec1[0] - fRec1[2])) - fConst5 * (fConst4 * fRec0[2] + fConst2 * fRec0[1]);
			float fTemp3 = fConst5 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp3);
			output1[i0] = FAUSTFLOAT(fTemp3);
			fVec0[1] = fVec0[0];
			iRec2[1] = iRec2[0];
			iRec3[1] = iRec3[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec6[1] = fRec6[0];
			IOTA0 = IOTA0 + 1;
			fRec5[2] = fRec5[1];
			fRec5[1] = fRec5[0];
			fRec4[2] = fRec4[1];
			fRec4[1] = fRec4[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
