/* ------------------------------------------------------------
name: "strings_stacc"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn StringsStacc -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __StringsStacc_H__
#define  __StringsStacc_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS StringsStacc
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

static float StringsStacc_faustpower2_f(float value) {
	return value * value;
}

class StringsStacc : public dsp {
	
 private:
	
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst4;
	float fConst5;
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iRec2[2];
	float fConst6;
	float fRec3[2];
	float fConst7;
	float fConst8;
	FAUSTFLOAT fHslider0;
	float fConst10;
	float fConst12;
	float fConst14;
	int iRec5[2];
	float fConst15;
	float fConst16;
	float fConst17;
	int iRec6[2];
	FAUSTFLOAT fHslider1;
	float fRec4[3];
	float fConst18;
	FAUSTFLOAT fHslider2;
	float fConst19;
	float fRec7[2];
	float fRec9[2];
	float fRec11[2];
	float fRec13[2];
	FAUSTFLOAT fHslider3;
	float fVec1[2];
	float fConst20;
	float fConst21;
	float fConst22;
	float fRec1[2];
	float fRec0[3];
	
 public:
	StringsStacc() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn StringsStacc -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "strings_stacc.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
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
		m->declare("name", "strings_stacc");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
		m->declare("oscillators.lib/version", "1.5.0");
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
		float fConst1 = std::tan(21991.148f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / StringsStacc_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -1.4142135f) / fConst1 + 1.0f;
		fConst5 = 1.0f / ((fConst3 + 1.4142135f) / fConst1 + 1.0f);
		fConst6 = 1.0f / std::max<float>(1.0f, 0.09f * fConst0);
		fConst7 = std::max<float>(1.0f, 0.008f * fConst0);
		fConst8 = 1.0f / fConst7;
		float fConst9 = std::tan(8796.459f / fConst0);
		fConst10 = 2.0f * (1.0f - 1.0f / StringsStacc_faustpower2_f(fConst9));
		float fConst11 = 1.0f / fConst9;
		fConst12 = (fConst11 + -0.5f) / fConst9 + 1.0f;
		float fConst13 = (fConst11 + 0.5f) / fConst9 + 1.0f;
		fConst14 = 1.0f / fConst13;
		fConst15 = std::max<float>(1.0f, 0.002f * fConst0);
		fConst16 = 1.0f / fConst15;
		fConst17 = 1.0f / std::max<float>(1.0f, 0.02f * fConst0);
		fConst18 = 1.0f / (fConst9 * fConst13);
		fConst19 = 1.0f / fConst0;
		fConst20 = 1.0f / std::tan(439.82297f / fConst0);
		fConst21 = 1.0f - fConst20;
		fConst22 = 1.0f / (fConst20 + 1.0f);
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.16f);
		fHslider1 = FAUSTFLOAT(0.18f);
		fHslider2 = FAUSTFLOAT(2.2e+02f);
		fHslider3 = FAUSTFLOAT(0.6f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec2[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fRec3[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec5[l3] = 0;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec6[l4] = 0;
		}
		for (int l5 = 0; l5 < 3; l5 = l5 + 1) {
			fRec4[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec7[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec9[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec11[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec13[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fVec1[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec1[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 3; l12 = l12 + 1) {
			fRec0[l12] = 0.0f;
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
	
	virtual StringsStacc* clone() {
		return new StringsStacc();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("strings_stacc");
		ui_interface->addHorizontalSlider("bite", &fHslider1, FAUSTFLOAT(0.18f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.5f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("decay", &fHslider0, FAUSTFLOAT(0.16f), FAUSTFLOAT(0.05f), FAUSTFLOAT(0.6f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider3, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow3 = 4.656613e-10f * float(fHslider1);
		float fSlow4 = float(fHslider2);
		float fSlow5 = std::max<float>(1.1920929e-07f, std::fabs(2.0f * fSlow4));
		float fSlow6 = fConst19 * fSlow5;
		float fSlow7 = 1.0f - fConst0 / fSlow5;
		float fSlow8 = std::max<float>(1.1920929e-07f, std::fabs(fSlow4));
		float fSlow9 = fConst19 * fSlow8;
		float fSlow10 = 1.0f - fConst0 / fSlow8;
		float fSlow11 = std::max<float>(1.1920929e-07f, std::fabs(0.997f * fSlow4));
		float fSlow12 = fConst19 * fSlow11;
		float fSlow13 = 1.0f - fConst0 / fSlow11;
		float fSlow14 = std::max<float>(1.1920929e-07f, std::fabs(1.003f * fSlow4));
		float fSlow15 = fConst19 * fSlow14;
		float fSlow16 = 1.0f - fConst0 / fSlow14;
		float fSlow17 = float(fHslider3);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow0;
			iRec2[0] = iSlow1 * (iRec2[1] + 1);
			fRec3[0] = fSlow0 + fRec3[1] * float(fVec0[1] >= fSlow0);
			iRec5[0] = (iRec5[1] + (iRec5[1] > 0)) * (fSlow0 <= fVec0[1]) + (fSlow0 > fVec0[1]);
			float fTemp0 = float(iRec5[0]);
			iRec6[0] = 1103515245 * iRec6[1] + 12345;
			fRec4[0] = fSlow3 * float(iRec6[0]) * std::max<float>(0.0f, std::min<float>(fConst16 * fTemp0, fConst17 * (fConst15 - fTemp0) + 1.0f)) - fConst14 * (fConst12 * fRec4[2] + fConst10 * fRec4[1]);
			float fTemp1 = fSlow6 + fRec7[1] + -1.0f;
			int iTemp2 = fTemp1 < 0.0f;
			float fTemp3 = fSlow6 + fRec7[1];
			fRec7[0] = ((iTemp2) ? fTemp3 : fTemp1);
			float fRec8 = ((iTemp2) ? fTemp3 : fSlow6 + fRec7[1] + fSlow7 * fTemp1);
			float fTemp4 = fSlow9 + fRec9[1] + -1.0f;
			int iTemp5 = fTemp4 < 0.0f;
			float fTemp6 = fSlow9 + fRec9[1];
			fRec9[0] = ((iTemp5) ? fTemp6 : fTemp4);
			float fRec10 = ((iTemp5) ? fTemp6 : fSlow9 + fRec9[1] + fSlow10 * fTemp4);
			float fTemp7 = fSlow12 + fRec11[1] + -1.0f;
			int iTemp8 = fTemp7 < 0.0f;
			float fTemp9 = fSlow12 + fRec11[1];
			fRec11[0] = ((iTemp8) ? fTemp9 : fTemp7);
			float fRec12 = ((iTemp8) ? fTemp9 : fSlow12 + fRec11[1] + fSlow13 * fTemp7);
			float fTemp10 = fSlow15 + fRec13[1] + -1.0f;
			int iTemp11 = fTemp10 < 0.0f;
			float fTemp12 = fSlow15 + fRec13[1];
			fRec13[0] = ((iTemp11) ? fTemp12 : fTemp10);
			float fRec14 = ((iTemp11) ? fTemp12 : fSlow15 + fRec13[1] + fSlow16 * fTemp10);
			float fTemp13 = fSlow17 * (0.30769232f * (2.0f * (fRec14 - (1.0f - (fRec12 + fRec10))) + 0.25f * (2.0f * fRec8 + -1.0f) + -1.0f) + fConst18 * (fRec4[0] - fRec4[2])) * std::max<float>(0.0f, std::min<float>(fConst8 * fRec3[0], std::max<float>(fSlow2 * (fConst7 - fRec3[0]) + 1.0f, 0.0f)) * (1.0f - fConst6 * float(iRec2[0])));
			fVec1[0] = fTemp13;
			fRec1[0] = -(fConst22 * (fConst21 * fRec1[1] - fConst20 * (fTemp13 - fVec1[1])));
			fRec0[0] = fRec1[0] - fConst5 * (fConst4 * fRec0[2] + fConst2 * fRec0[1]);
			float fTemp14 = fConst5 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp14);
			output1[i0] = FAUSTFLOAT(fTemp14);
			fVec0[1] = fVec0[0];
			iRec2[1] = iRec2[0];
			fRec3[1] = fRec3[0];
			iRec5[1] = iRec5[0];
			iRec6[1] = iRec6[0];
			fRec4[2] = fRec4[1];
			fRec4[1] = fRec4[0];
			fRec7[1] = fRec7[0];
			fRec9[1] = fRec9[0];
			fRec11[1] = fRec11[0];
			fRec13[1] = fRec13[0];
			fVec1[1] = fVec1[0];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
