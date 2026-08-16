/* ------------------------------------------------------------
name: "fx_bass_grit"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FxBassGrit -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FxBassGrit_H__
#define  __FxBassGrit_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FxBassGrit
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

static float FxBassGrit_faustpower2_f(float value) {
	return value * value;
}

class FxBassGrit : public dsp {
	
 private:
	
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst1;
	float fVec0[2];
	float fRec1[2];
	float fRec0[3];
	float fRec3[2];
	float fRec2[3];
	float fConst3;
	float fConst7;
	float fConst8;
	float fConst11;
	float fConst12;
	float fConst13;
	float fConst15;
	float fConst16;
	float fConst17;
	FAUSTFLOAT fHslider1;
	float fRec8[2];
	float fVec1[2];
	float fVec2[2];
	float fConst18;
	float fConst19;
	float fRec7[2];
	float fRec6[3];
	float fConst20;
	float fRec5[3];
	float fConst22;
	float fConst23;
	float fVec3[2];
	float fConst25;
	float fConst26;
	float fRec4[2];
	FAUSTFLOAT fHslider2;
	float fVec4[2];
	float fRec10[2];
	float fRec9[3];
	float fRec12[2];
	float fRec11[3];
	float fVec5[2];
	float fVec6[2];
	float fRec16[2];
	float fRec15[3];
	float fRec14[3];
	float fVec7[2];
	float fRec13[2];
	
 public:
	FxBassGrit() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FxBassGrit -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("filename", "fx_bass_grit.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/peak_eq:author", "Julius O. Smith III");
		m->declare("filters.lib/peak_eq:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/peak_eq:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "fx_bass_grit");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
		m->declare("signals.lib/name", "Faust Signal Routing Library");
		m->declare("signals.lib/version", "1.5.0");
	}

	virtual int getNumInputs() {
		return 2;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		float fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 3.1415927f / fConst0;
		float fConst2 = std::tan(3141.5928f / fConst0);
		fConst3 = 2.0f * (1.0f - 1.0f / FxBassGrit_faustpower2_f(fConst2));
		float fConst4 = fConst0 * std::sin(6283.1855f / fConst0);
		float fConst5 = 2513.2742f / fConst4;
		float fConst6 = 1.0f / fConst2;
		fConst7 = (fConst6 - fConst5) / fConst2 + 1.0f;
		fConst8 = 1.0f / ((fConst6 + fConst5) / fConst2 + 1.0f);
		float fConst9 = std::tan(691.1504f / fConst0);
		float fConst10 = FxBassGrit_faustpower2_f(fConst9);
		fConst11 = 2.0f * (1.0f - 1.0f / fConst10);
		fConst12 = 1.0f / fConst9;
		fConst13 = (fConst12 + -1.0f) / fConst9 + 1.0f;
		float fConst14 = (fConst12 + 1.0f) / fConst9 + 1.0f;
		fConst15 = 1.0f / fConst14;
		fConst16 = 44.1f / fConst0;
		fConst17 = 1.0f - fConst16;
		fConst18 = 1.0f - fConst12;
		fConst19 = 1.0f / (fConst12 + 1.0f);
		fConst20 = 1.0f / (fConst10 * fConst14);
		float fConst21 = 3983.271f / fConst4;
		fConst22 = (fConst6 - fConst21) / fConst2 + 1.0f;
		fConst23 = (fConst6 + fConst21) / fConst2 + 1.0f;
		float fConst24 = 1.0f / std::tan(20420.352f / fConst0);
		fConst25 = 1.0f - fConst24;
		fConst26 = 1.0f / (fConst24 + 1.0f);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(1.2e+02f);
		fHslider1 = FAUSTFLOAT(9.0f);
		fHslider2 = FAUSTFLOAT(0.5f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fRec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 3; l2 = l2 + 1) {
			fRec0[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec3[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec8[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fVec1[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fVec2[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec7[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 3; l9 = l9 + 1) {
			fRec6[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 3; l10 = l10 + 1) {
			fRec5[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fVec3[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec4[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fVec4[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 2; l14 = l14 + 1) {
			fRec10[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 3; l15 = l15 + 1) {
			fRec9[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 2; l16 = l16 + 1) {
			fRec12[l16] = 0.0f;
		}
		for (int l17 = 0; l17 < 3; l17 = l17 + 1) {
			fRec11[l17] = 0.0f;
		}
		for (int l18 = 0; l18 < 2; l18 = l18 + 1) {
			fVec5[l18] = 0.0f;
		}
		for (int l19 = 0; l19 < 2; l19 = l19 + 1) {
			fVec6[l19] = 0.0f;
		}
		for (int l20 = 0; l20 < 2; l20 = l20 + 1) {
			fRec16[l20] = 0.0f;
		}
		for (int l21 = 0; l21 < 3; l21 = l21 + 1) {
			fRec15[l21] = 0.0f;
		}
		for (int l22 = 0; l22 < 3; l22 = l22 + 1) {
			fRec14[l22] = 0.0f;
		}
		for (int l23 = 0; l23 < 2; l23 = l23 + 1) {
			fVec7[l23] = 0.0f;
		}
		for (int l24 = 0; l24 < 2; l24 = l24 + 1) {
			fRec13[l24] = 0.0f;
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
	
	virtual FxBassGrit* clone() {
		return new FxBassGrit();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fx_bass_grit");
		ui_interface->addHorizontalSlider("drive", &fHslider1, FAUSTFLOAT(9.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(24.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("grit", &fHslider2, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("xover", &fHslider0, FAUSTFLOAT(1.2e+02f), FAUSTFLOAT(6e+01f), FAUSTFLOAT(2e+02f), FAUSTFLOAT(1.0f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* input0 = inputs[0];
		FAUSTFLOAT* input1 = inputs[1];
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::tan(fConst1 * float(fHslider0));
		float fSlow1 = 1.0f / FxBassGrit_faustpower2_f(fSlow0);
		float fSlow2 = 2.0f * (1.0f - fSlow1);
		float fSlow3 = 1.0f / fSlow0;
		float fSlow4 = (fSlow3 + -1.0f) / fSlow0 + 1.0f;
		float fSlow5 = 1.0f / ((fSlow3 + 1.0f) / fSlow0 + 1.0f);
		float fSlow6 = 1.0f - fSlow3;
		float fSlow7 = 1.0f / (fSlow3 + 1.0f);
		float fSlow8 = fConst16 * std::pow(1e+01f, 0.05f * float(fHslider1));
		float fSlow9 = 0.5f * float(fHslider2);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			float fTemp0 = float(input0[i0]);
			fVec0[0] = fTemp0;
			fRec1[0] = -(fSlow7 * (fSlow6 * fRec1[1] - fSlow3 * (fTemp0 - fVec0[1])));
			fRec0[0] = fRec1[0] - fSlow5 * (fSlow4 * fRec0[2] + fSlow2 * fRec0[1]);
			fRec3[0] = -(fSlow7 * (fSlow6 * fRec3[1] - (fTemp0 + fVec0[1])));
			fRec2[0] = fRec3[0] - fSlow5 * (fSlow4 * fRec2[2] + fSlow2 * fRec2[1]);
			float fTemp1 = fConst3 * fRec5[1];
			fRec8[0] = fSlow8 + fConst17 * fRec8[1];
			float fTemp2 = fTemp0 * fRec8[0];
			fVec1[0] = fTemp2;
			float fTemp3 = fTemp2 - fVec1[1];
			float fTemp4 = std::fabs(fVec1[1]);
			float fTemp5 = std::fabs(fTemp2);
			float fTemp6 = ((std::fabs(fTemp3) < 0.0001f) ? tanhf(0.5f * (fTemp2 + fVec1[1])) : (fTemp5 + std::log(std::exp(-(2.0f * fTemp5)) + 1.0f) - (fTemp4 + std::log(std::exp(-(2.0f * fTemp4)) + 1.0f))) / (fTemp2 + 1e-30f * float(fTemp3 == 0.0f) - fVec1[1]));
			fVec2[0] = fTemp6;
			fRec7[0] = -(fConst19 * (fConst18 * fRec7[1] - fConst12 * (fTemp6 - fVec2[1])));
			fRec6[0] = fRec7[0] - fConst15 * (fConst13 * fRec6[2] + fConst11 * fRec6[1]);
			fRec5[0] = fConst20 * (fRec6[2] + (fRec6[0] - 2.0f * fRec6[1])) - fConst8 * (fConst7 * fRec5[2] + fTemp1);
			float fTemp7 = fTemp1 + fConst23 * fRec5[0] + fConst22 * fRec5[2];
			fVec3[0] = fTemp7;
			fRec4[0] = -(fConst26 * (fConst25 * fRec4[1] - fConst8 * (fTemp7 + fVec3[1])));
			output0[i0] = FAUSTFLOAT(fSlow9 * fRec4[0] + fSlow5 * (fRec2[2] + fRec2[0] + 2.0f * fRec2[1] + fSlow1 * (fRec0[0] + fRec0[2] - 2.0f * fRec0[1])));
			float fTemp8 = float(input1[i0]);
			fVec4[0] = fTemp8;
			fRec10[0] = -(fSlow7 * (fSlow6 * fRec10[1] - fSlow3 * (fTemp8 - fVec4[1])));
			fRec9[0] = fRec10[0] - fSlow5 * (fSlow4 * fRec9[2] + fSlow2 * fRec9[1]);
			fRec12[0] = -(fSlow7 * (fSlow6 * fRec12[1] - (fTemp8 + fVec4[1])));
			fRec11[0] = fRec12[0] - fSlow5 * (fSlow4 * fRec11[2] + fSlow2 * fRec11[1]);
			float fTemp9 = fConst3 * fRec14[1];
			float fTemp10 = fTemp8 * fRec8[0];
			fVec5[0] = fTemp10;
			float fTemp11 = fTemp10 - fVec5[1];
			float fTemp12 = std::fabs(fVec5[1]);
			float fTemp13 = std::fabs(fTemp10);
			float fTemp14 = ((std::fabs(fTemp11) < 0.0001f) ? tanhf(0.5f * (fTemp10 + fVec5[1])) : (fTemp13 + std::log(std::exp(-(2.0f * fTemp13)) + 1.0f) - (fTemp12 + std::log(std::exp(-(2.0f * fTemp12)) + 1.0f))) / (fTemp10 + 1e-30f * float(fTemp11 == 0.0f) - fVec5[1]));
			fVec6[0] = fTemp14;
			fRec16[0] = -(fConst19 * (fConst18 * fRec16[1] - fConst12 * (fTemp14 - fVec6[1])));
			fRec15[0] = fRec16[0] - fConst15 * (fConst13 * fRec15[2] + fConst11 * fRec15[1]);
			fRec14[0] = fConst20 * (fRec15[2] + (fRec15[0] - 2.0f * fRec15[1])) - fConst8 * (fConst7 * fRec14[2] + fTemp9);
			float fTemp15 = fTemp9 + fConst23 * fRec14[0] + fConst22 * fRec14[2];
			fVec7[0] = fTemp15;
			fRec13[0] = -(fConst26 * (fConst25 * fRec13[1] - fConst8 * (fTemp15 + fVec7[1])));
			output1[i0] = FAUSTFLOAT(fSlow9 * fRec13[0] + fSlow5 * (fRec11[2] + fRec11[0] + 2.0f * fRec11[1] + fSlow1 * (fRec9[0] + fRec9[2] - 2.0f * fRec9[1])));
			fVec0[1] = fVec0[0];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
			fRec3[1] = fRec3[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			fRec8[1] = fRec8[0];
			fVec1[1] = fVec1[0];
			fVec2[1] = fVec2[0];
			fRec7[1] = fRec7[0];
			fRec6[2] = fRec6[1];
			fRec6[1] = fRec6[0];
			fRec5[2] = fRec5[1];
			fRec5[1] = fRec5[0];
			fVec3[1] = fVec3[0];
			fRec4[1] = fRec4[0];
			fVec4[1] = fVec4[0];
			fRec10[1] = fRec10[0];
			fRec9[2] = fRec9[1];
			fRec9[1] = fRec9[0];
			fRec12[1] = fRec12[0];
			fRec11[2] = fRec11[1];
			fRec11[1] = fRec11[0];
			fVec5[1] = fVec5[0];
			fVec6[1] = fVec6[0];
			fRec16[1] = fRec16[0];
			fRec15[2] = fRec15[1];
			fRec15[1] = fRec15[0];
			fRec14[2] = fRec14[1];
			fRec14[1] = fRec14[0];
			fVec7[1] = fVec7[0];
			fRec13[1] = fRec13[0];
		}
	}

};

#endif
